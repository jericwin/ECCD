using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class LearnerConfiguration : IEntityTypeConfiguration<Learner>
{
    public void Configure(EntityTypeBuilder<Learner> builder)
    {
        builder.HasKey(l => l.Id);

        builder.Property(l => l.FirstName).HasMaxLength(100).IsRequired();
        builder.Property(l => l.LastName).HasMaxLength(100).IsRequired();
        builder.Property(l => l.LearnerIdCode).HasMaxLength(50).IsRequired();
        builder.Property(l => l.PhotoUrl).HasMaxLength(500);

        builder.HasIndex(l => l.LearnerIdCode).IsUnique();

        builder.HasOne(l => l.Parent)
            .WithMany(p => p.Learners)
            .HasForeignKey(l => l.ParentId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(l => l.Cdc)
            .WithMany(c => c.Learners)
            .HasForeignKey(l => l.CdcId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasQueryFilter(l => !l.IsDeleted);
    }
}
