using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class ParentProfileConfiguration : IEntityTypeConfiguration<ParentProfile>
{
    public void Configure(EntityTypeBuilder<ParentProfile> builder)
    {
        builder.HasKey(p => p.Id);

        builder.Property(p => p.FullName).HasMaxLength(200).IsRequired();
        builder.Property(p => p.RelationshipToLearner).HasMaxLength(50).IsRequired();
        builder.Property(p => p.Mobile).HasMaxLength(20);
        builder.Property(p => p.Address).HasMaxLength(500);
        builder.Property(p => p.UserId).HasMaxLength(450).IsRequired();

        builder.HasIndex(p => p.UserId).IsUnique();
    }
}
